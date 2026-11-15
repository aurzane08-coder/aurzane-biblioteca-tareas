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
