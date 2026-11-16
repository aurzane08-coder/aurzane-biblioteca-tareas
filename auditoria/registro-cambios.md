# Registro de cambios UX/UI (15 de noviembre de 2026)

Copia de seguridad previa: `www/copias/20261115-1543/` en el servidor (todas las webs, sin vídeos ni zip).
Cada archivo sustituido queda también en `publicado/<fecha>/` de este repositorio, y los parches de texto guardan el original en `<web>/eliminar/<parche>-<fecha>/`.

## Archivos nuevos
- `aurzane.com/aurzane-ds.css`: sistema de diseño común (tokens de color por mundo, foco visible, objetivos de 24 px, movimiento reducido, barra del ecosistema, buscador global, contraste).
- `aurzane.com/aurzane-ds.js`: barra común del ecosistema, buscador global (Ctrl+K) con índice de 102 páginas, enlace «Saltar al contenido», nombres accesibles, `inert` en zonas ocultas.
- `ai/parches/cifras.py` + `.github/workflows/cifras.yml`: copia cada día el número real de universidades del catálogo a las páginas que lo citan.
- `.github/workflows/auditoria.yml`, `auditoria/auditar.js`, `auditoria/urls.txt`: auditoría automática (Playwright + axe, 8 anchos).
- `.github/workflows/copia-y-mapa.yml`, `.github/workflows/consulta.yml`.

## Archivos modificados
- `aurzane.com/aurzane-paleta.js`: carga `aurzane-ds.css` y `aurzane-ds.js`; `aurzane-estilo.js` pasa a v=22.
- `aurzane.com/aurzane-estilo.js`: fotos reales de Unsplash en lugar de dibujos propios (portada de cada test y calculadora, «Sigue explorando», emblema de mundo retirado); pie legal que ya no desborda en móvil; contraste del enlace «Avísanos»; cifra de universidades.
- `aurzane.com/index.html`: nueva sección «¿Qué quieres hacer hoy?» tras la cabecera; tuteo; cifra de universidades.
- `ai/parches/voseo.py`: frases revisadas en contexto y OVP incluido (19 archivos corregidos en el servidor).
- Por `cifras.py` en el servidor: `aurzane.com/index.html`, `aurzane.com/aurzane-estilo.js`, `nexus.aurzane.com/index.html`, `nexus.aurzane.com/nexus-biblioteca.html`.

## No se ha tocado
Preguntas, puntuaciones, fórmulas y resultados de tests y calculadoras; datos de herramientas; reglas de negocio; datos de usuarios.

## Segunda ronda (tras la primera auditoría «después»)
- `aurzane-ds.css` v2: la barra común ya no hereda estilos de listas de cada página (Novedades), anchos móviles (Research Hub, Contacto, artículos, calculadoras de BUILD, test de personalidad), contraste de etiquetas de la portada, chip activo, enlaces de fuentes y objetivos de 24 px.
- `aurzane-estilo.js` v23: contraste del texto del panel «Empieza por aquí» y del enlace «Ver el curso».
- `aurzane-paleta.js`: versiones nuevas para que los navegadores recojan los cambios.

## Tercera ronda: cabecera única, pie único y portada nueva (15/11/2026, tarde)
- `aurzane-ds.js` v3: una sola cabecera en todo el ecosistema (fila 1: AURZANE, mundos, buscar, cuenta y tema; fila 2: secciones del mundo actual). Se ocultan sin borrarse la barra de mundos, las cabeceras propias de cada plantilla, los paneles «Todo» y el megamenú antiguo. El aula de cursos y las pruebas OVP conservan su barra de trabajo.
- Pie único con mundos, conocimiento, cuenta, redes y legal; los pies de cada plantilla conservan sus avisos y pierden los enlaces repetidos.
- Portadas de mundo: foto real en la cabecera, sin «Sigue explorando en otros mundos» ni «Lo que X podría construir».
- Portada de aurzane.com rehecha desde `portada/generar.py` (+ `portada.css`, `portada.js`): cabecera con foto y buscador, seis necesidades, Hoy en AURZANE, tests con foto, ejercicios, orientación, calculadoras, cursos, biblioteca, novedades del feed, confianza y preguntas frecuentes. Cifras de libros, tests y artículos leídas de datos reales.
- Fichas `ref-*.html` duplicadas y rotas en la raíz: redirección 301 a su ficha de la biblioteca y copia movida a eliminar (`parche-ref.yml`).
- Auditoría total: 142 páginas (todas las de cada mundo y muestras de cada plantilla generada), 4 anchos, axe.

## Cuarta ronda: revisión total página a página (15/11/2026, noche)
Revisadas las 140 plantillas auditadas en escritorio y móvil, con capturas completas.
- Cabecera: la segunda fila de aurzane.com solo aparece en las páginas de conocimiento (biblioteca, libros, artículos, Research Hub, frases, novedades, temas y mapa); la cuenta, el contacto y lo legal ya no la repiten.
- Pie: se ocultan los pies mínimos de plantilla (correo + ©) que repetían el pie común (Mi AURZANE, portal OVP).
- Portadas de mundo: se ocultan los accesos rápidos (Guías, Mis guardados, Biblioteca, Ecosistema…) que repetían la navegación.
- Tarjetas de tests y calculadoras: foto real en lugar de emoji en portadas de mundo y «Más herramientas» (`aurzane-estilo.js` v24).
- Calculadoras: cada una con su foto (agua, calorías, IMC, embarazo, edad, días entre fechas, porcentajes, sueldo neto, nota PAU); antes muchas repetían la misma.
- Biblioteca y tienda: el librero pasa al final del contenido en lugar de aparecer antes del libro o del catálogo.
- Tests en inglés y portugués: plantilla nueva igual a la de los tests en español (cabecera morada con foto, preguntas en tarjeta, resultado al lado). Preguntas, opciones, puntuación y niveles sin cambios (`tests_en/gen.py`, `tests_pt/gen.py`).
- Mapa del sitio: cada página con su título real, agrupada por mundo y tipo (`ai/manager.py`).
- Portada: la foto del test de personalidad ya no ocupa media pantalla.
- Tuteo: 12 frases más (Mi AURZANE, OVP, NEXUS).
- Contraste y anchos: informe OVP de ejemplo, «Volver» de los artículos de mundo, libros abiertos recientes en móvil, aviso de traducción.
- Auditoría: recorre cada página antes de capturarla para que carguen las imágenes diferidas; añadidos los 11 perfiles del test de personalidad.
- Ronda 5: portadas de mundo sin «Más explorado» (repetía artículos) ni la promoción duplicada de OVP; pies propios de cada mundo ocultos (el pie común ya los cubre); tienda de libros legible a 320 px; cinco rasgos de personalidad en una columna en pantallas muy estrechas; el aviso del boletín ya no tapa el contenido en móvil; casillas del boletín de 20 px; bandas del informe OVP con contraste; títulos limpios en el mapa del sitio; cabecera CORS para los estilos comunes (`parche-cors.yml`).

## Guardados comunes (15/11/2026, noche)
- Botón «Guardar» en la cabecera de cada test, perfil, calculadora, ejercicio, curso, libro, artículo y universidad, y botón «Guardados» con el número de elementos y un panel con todo lo guardado, agrupado por tipo y con el color de su mundo.
- Una sola lista para todo el ecosistema: se guarda en este navegador mediante `aurzane.com/guardados-almacen.html` (marco invisible que comparten todos los subdominios) y, con sesión de AURZANE ID, en la tabla `public.guardados` de Supabase (seguridad por filas: cada persona solo ve y cambia lo suyo) para tenerla en todos los dispositivos.
- Incorpora lo ya guardado en MIND, LIVE, LEARN, BUILD y NEXUS y en «Mi lista» del Research Hub, y mantiene ambas cosas sincronizadas al guardar o quitar.
- Se quita «Guardados» de la segunda fila de cada mundo (ahora está en la cabecera común).
- Informe OVP de ejemplo: marcas de las recomendaciones con contraste suficiente.

## Panel OVP v3 (15/11/2026, noche)
- `ovp.aurzane.com/portal.html` (generado con `ovp-panel/aplicar.py` + `panel.js` + `panel.css`): menú de 5 secciones (Inicio, Evaluaciones, Mi informe, Dónde estudiar, Mi cuenta); «Mi Proceso» se une a Evaluaciones; fuera la marca y los enlaces del ecosistema repetidos en la barra lateral y la ruta de navegación.
- Inicio: siguiente paso con una sola acción principal, anillo de progreso con el tiempo que queda (minutos reales de cada test), recorrido de 5 pasos y mosaico de evaluaciones con icono, estado y acceso directo.
- Nueva sección «Dónde estudiar»: las carreras del informe (CHASIDE u Holland) enlazan a NEXUS «¿Qué puedo estudiar?» filtrado por carrera y, si la pones, por tu nota; herramientas de notas de corte, universidades y calculadora PAU. Banda al final del informe que lleva ahí.
- Móvil: pestañas horizontales en lugar del segundo menú; corregido el menú móvil que aparecía visible en escritorio.
- NEXUS `que-puedo-estudiar` acepta `?carrera=`, `?q=` y `?cc=` (`univ/gen/gen.py`).

## Revisión del 16/11/2026 (mañana)
- Sin nombre del titular en las páginas públicas (`ai/parches/nombre.py`, cada día): tests, ejercicios, calculadoras, guías, EN/PT, Sobre AURZANE, contacto, condiciones, política editorial y colegios. Se mantiene solo en el aviso legal y la política de privacidad (lo exige la ley) y en documentos firmados (certificados de LEARN e informes de OVP). Generadores corregidos en origen (`guias/guias.py`, `tests_en/gen.py`, `tests_pt/gen.py`).
- Admin fuera de Google: cabecera `X-Robots-Tag: noindex` comprobada en `admin.html` y `admin-cursos.html` (parche de seguridad diario).
- Colegios: panel del colegio (`ovp.aurzane.com/colegio.html`) con alta y baja del equipo del colegio desde la vista de administración; página de colegios con «Entrar al panel del colegio» y los dos accesos explicados; el estudiante decide si comparte su informe desde «Mi cuenta».
- Cifras: la tienda cuenta los libros gratis igual que la biblioteca y la portada; las cifras se corrigen también tras publicar universidades y la tienda, y en biblioteca, colegios, Sobre AURZANE y OVP (países y universidades exactos).
- Identidad: el parche de mundos cambia también «Vida sin límites», «Imperio físico» y «NEXUS: tecnología…» que quedaban en /temas/.
- Lenguaje: los artículos de la IA se publican ya en tuteo (mismas listas que el parche de voseo).
- Colegios (segunda parte, `ovp-panel/colegios2.sql`, ejecutado en Supabase): cada colegio tiene enfoque «general» o «militar» (COMIL 12 queda en militar); el informe solo añade la sección militar si el colegio es militar. Nadie puede ponerse el membrete de un colegio desde su informe (antes se podía elegir en el selector). El colegio o la administración pueden «Quitar del colegio» a quien no sea suyo: pasa al informe general de AURZANE y no puede volver a entrar con ese enlace. La administración da de alta y edita colegios desde el panel del colegio (enlace «Colegios» añadido al admin).
- Biblioteca (`aurzane-bib.js`, cargado por la capa común): sugerencias al escribir en el buscador (libros y temas, con teclado), «Leer aquí» y «Ficha» bien diferenciados, aviso claro en cada libro (se lee aquí o es una ficha), «Seguir leyendo» con la página por la que vas y estantería con tus libros guardados, botones del lector más grandes en el móvil.
- LEARN (`aurzane-learn.js`, cargado por la capa común): panel «Tu aprendizaje» en la portada de LEARN y en el catálogo con cada curso empezado (lecciones abiertas, evaluación final, certificado), «Continuar» en la lección donde lo dejaste y los cursos completados; en la página de cada curso, tu avance y «Continuar el curso». Nuevo «Mi aprendizaje» en la navegación de LEARN.
- Seguridad v2: el almacén común de «Guardados» se puede abrir solo desde aurzane.com y sus subdominios (frame-ancestors); antes la cabecera X-Frame-Options lo bloqueaba en MIND, LIVE, LEARN, NEXUS y BUILD. Auditoría de comprobación (`bib-learn-despues`): 13 páginas en 375 y 1366 px, sin desbordes ni fallos de accesibilidad.

## 16/11/2026, mañana (2)
- Awin: aceptada la invitación de World Businesses for Sale y fanmuebles (aceptado al momento); solicitados Leroy Merlin, Decathlon, Viator, Logitravel, SaludOnNet y ERGO Seguros de Viaje. Cada uno tiene su sitio en `aurzane-estilo.js` (v25): si el socio principal de una página aún no nos acepta, aparece el siguiente que encaje. Los bloques solo se muestran cuando Awin confirma la aceptación (lo comprueba la tienda cada día).
- Textos legales rehechos (`legal/textos.py` + `legal/gen.py`): privacidad (AURZANE ID, Guardados, cursos, certificados, OVP, colegios, IA, proveedores, menores, derechos), cookies (cookies y almacenamiento del navegador, uno por uno), condiciones de uso (Guardados, cursos no reglados, colegios, afiliados) y aviso legal. Sobre AURZANE, contacto y política editorial sin el nombre del titular.
