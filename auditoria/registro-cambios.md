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
