"""Research Hub en inglés (aurzane.com/en/research.html), 23/11/2026.
Los papers ya están en inglés: se traduce la interfaz. La página inglesa se genera cada día a partir de la española
(research.html del servidor), así cualquier mejora de la española llega sola a la inglesa.
traducir(t) cambia los textos de la interfaz; prerender.py rellena después los bloques con datos en inglés.
Si algún texto de la página española cambia y ya no se encuentra aquí, sale un aviso en el registro de la acción
(la página se publica igual, con ese texto en español, hasta que se añada a la tabla)."""
import re

URL_ES = 'https://aurzane.com/research.html'
URL_EN = 'https://aurzane.com/en/research.html'

# (español, inglés). Frases completas o con su contexto para no tocar el código.
T = [
    # cabecera de la página
    ('<html lang="es"', '<html lang="en"'),
    ('<meta name="description" content="Un solo buscador para las cinco bibliotecas académicas de AURZANE: 25.000 artículos científicos de acceso abierto de Mind, Nexus, Live, Learn y Build, con abstract y fuente citable.">',
     '<meta name="description" content="One search for the five academic libraries of AURZANE: thousands of open access scientific papers on psychology, education, health, society and technology, each with its official abstract and a citable source.">'),
    ('<title>Research Hub | AURZANE</title>', '<title>Research Hub: search open access papers | AURZANE</title>'),
    ("'Error desconocido'", "'Unknown error'"),
    ("'Promise rechazada'", "'Rejected promise'"),
    # barra superior
    ('<a href="https://aurzane.com">Inicio</a>', '<a href="https://aurzane.com">Home</a>'),
    ('<a href="https://aurzane.com/#research">Cómo trabajamos</a>', '<a href="https://aurzane.com/#research">How we work</a>'),
    # portada del buscador
    ('<h1>Un solo buscador para <span>toda la investigación de AURZANE</span></h1>', '<h1>One search for <span>all of AURZANE\'s research</span></h1>'),
    ('<p>Las cinco bibliotecas académicas de AURZANE en un solo lugar: título, resumen oficial y enlace directo a la fuente de cada paper.</p>',
     '<p>The five academic libraries of AURZANE in one place: the title, the official abstract and a direct link to the source of every paper.</p>'),
    ('placeholder="Busca por tema, palabra clave o pregunta"', 'placeholder="Search by topic, keyword or question"'),
    ('aria-label="Borrar búsqueda"', 'aria-label="Clear search"'),
    ('<span class="txt">Buscar</span>', '<span class="txt">Search</span>'),
    ('<p class="search-hint">Los papers están en su idioma original, casi siempre inglés. Si buscas en español, también buscamos la traducción. Pulsa <kbd>/</kbd> para buscar y <kbd>↑</kbd> <kbd>↓</kbd> para elegir una sugerencia.</p>',
     '<p class="search-hint">Papers are shown in their original language, almost always English. Press <kbd>/</kbd> to search and <kbd>↑</kbd> <kbd>↓</kbd> to pick a suggestion.</p>'),
    ('<summary>Consejos para buscar mejor', '<summary>Search tips'),
    ('<code>"sleep quality"</code> busca la frase exacta.', '<code>"sleep quality"</code> finds the exact phrase.'),
    ('<code>anxiety or stress</code> encuentra papers con cualquiera de las dos palabras.', '<code>anxiety or stress</code> finds papers with either word.'),
    ('<code>memory -children</code> excluye los papers que mencionan la segunda palabra.', '<code>memory -children</code> leaves out papers that mention the second word.'),
    ('<li>Combina la búsqueda con los filtros de mundo, año, autor y acceso abierto.</li>', '<li>Combine your search with the world, year, author and open access filters.</li>'),
    ('<li>Pulsa «Guardar» en los papers que te interesen y expórtalos desde «Mi lista» a Zotero, Mendeley o EndNote (RIS o BibTeX).</li>',
     '<li>Press “Save” on the papers you like and export them from “My list” to Zotero, Mendeley or EndNote (RIS or BibTeX).</li>'),
    ('Foto de cabecera: <a href="https://unsplash.com/es"', 'Header photo: <a href="https://unsplash.com"'),
    # mundos
    ('<h2 id="t-mundos">Explora por mundo</h2>', '<h2 id="t-mundos">Explore by world</h2>'),
    ('<p>Cada mundo de AURZANE tiene su propia biblioteca científica. Elige uno para ver solo sus papers.</p>',
     '<p>Each AURZANE world has its own scientific library. Pick one to see only its papers.</p>'),
    ('Fotos de Unsplash, las mismas que identifican cada mundo en AURZANE.', 'Photos from Unsplash, the same ones that identify each world on AURZANE.'),
    # filtros
    ('aria-label="Filtros"', 'aria-label="Filters"'),
    ('<h2>Filtros</h2>', '<h2>Filters</h2>'),
    ('data-accion="limpiar" hidden>Quitar todos</button>', 'data-accion="limpiar" hidden>Clear all</button>'),
    ('id="t-cat">CATEGORÍA</span>', 'id="t-cat">WORLD</span>'),
    ('aria-pressed="true">Todas</button>', 'aria-pressed="true">All</button>'),
    ('id="t-anio">AÑO DE PUBLICACIÓN</span>', 'id="t-anio">PUBLICATION YEAR</span>'),
    ('for="anioDesde">Desde</label>', 'for="anioDesde">From</label>'),
    ('<option value="">Desde</option>', '<option value="">From</option>'),
    ('<span>a</span>', '<span>to</span>'),
    ('for="anioHasta">Hasta</label>', 'for="anioHasta">To</label>'),
    ('<option value="">Hasta</option>', '<option value="">To</option>'),
    ('for="autorInput">AUTOR</label>', 'for="autorInput">AUTHOR</label>'),
    ('placeholder="Apellido, por ejemplo Smith"', 'placeholder="Surname, for example Smith"'),
    ('<span>Solo acceso abierto</span>', '<span>Open access only</span>'),
    ('id="btnVerResultados">Ver resultados</button>', 'id="btnVerResultados">Show results</button>'),
    # barra de resultados
    ('id="btnEnlace">Copiar enlace de esta búsqueda</button>', 'id="btnEnlace">Copy link to this search</button>'),
    ('</svg>Filtros <span class="n" id="nFiltros">', '</svg>Filters <span class="n" id="nFiltros">'),
    ('<span>Ordenar por</span>', '<span>Sort by</span>'),
    ('<option value="recientes">Más recientes</option>', '<option value="recientes">Newest first</option>'),
    ('<option value="antiguos">Más antiguos</option>', '<option value="antiguos">Oldest first</option>'),
    ('<option value="titulo">Título (A a Z)</option>', '<option value="titulo">Title (A to Z)</option>'),
    ('Has llegado al final de los resultados.', 'You have reached the end of the results.'),
    ('aria-label="Volver arriba"', 'aria-label="Back to top"'),
    ('<p>Este Research Hub muestra el título y el abstract oficial de cada paper tal como se publicó, sin reescritura. Es un índice de referencia, no contenido editorial de AURZANE. Cada resultado enlaza a la fuente original. Si prefieres explorar un mundo a la vez, cada uno tiene su propia biblioteca:',
     '<p>This Research Hub shows the title and the official abstract of each paper exactly as published, without rewriting. It is a reference index, not AURZANE editorial content. Every result links to the original source. If you prefer to explore one world at a time, each has its own library (in Spanish):'),
    # textos que pinta el programa de la página
    ("toLocaleString('es-ES'", "toLocaleString('en-US'"),
    ("p.anio || 's. f.'", "p.anio || 'n.d.'"),
    ('<span class="mas">Autores no disponibles</span>', '<span class="mas">Authors not available</span>'),
    ('">y ${l.length - 3} autores más</button>', '">and ${l.length - 3} more authors</button>'),
    ('</svg>Acceso abierto</span>', '</svg>Open access</span>'),
    ('Leer resumen completo <svg', 'Read full abstract <svg'),
    ('<p><em>Este paper no tiene resumen disponible.</em></p>', '<p><em>This paper has no abstract available.</em></p>'),
    ('<span class="doi">Sin DOI</span>', '<span class="doi">No DOI</span>'),
    ('data-copiar="${esc(p.doi)}">Copiar DOI</button>', 'data-copiar="${esc(p.doi)}">Copy DOI</button>'),
    ('data-copiar-cita>Copiar cita</button>', 'data-copiar-cita>Copy citation</button>'),
    ('rel="noopener noreferrer">Leer artículo</a>', 'rel="noopener noreferrer">Read paper</a>'),
    ('`Novedades de los cinco mundos · <b>${num(mostrados)}</b> de ${num(t)} papers`', '`Latest from the five worlds · <b>${num(mostrados)}</b> of ${num(t)} papers`'),
    ("${t === 1 ? 'resultado' : 'resultados'}${estado.q ? ` para «${esc(estado.q)}»` : ''}", "${t === 1 ? 'result' : 'results'}${estado.q ? ` for “${esc(estado.q)}”` : ''}"),
    ("a.push(['q', `«${estado.q}»`])", "a.push(['q', `“${estado.q}”`])"),
    ('`${estado.desde} a ${estado.hasta}` : estado.desde ? `Desde ${estado.desde}` : `Hasta ${estado.hasta}`', '`${estado.desde} to ${estado.hasta}` : estado.desde ? `From ${estado.desde}` : `Until ${estado.hasta}`'),
    ("a.push(['autor', `Autor: ${estado.autor}`])", "a.push(['autor', `Author: ${estado.autor}`])"),
    ("a.push(['oa', 'Acceso abierto'])", "a.push(['oa', 'Open access'])"),
    ('aria-label="Quitar filtro ${esc(t)}"', 'aria-label="Remove filter ${esc(t)}"'),
    ("textContent = 'Cargando…'", "textContent = 'Loading…'"),
    ("textContent = 'Cargar más resultados'", "textContent = 'Load more results'"),
    ('<span class="txt">Cargar más resultados</span>', '<span class="txt">Load more results</span>'),
    ("textContent = 'Copiado'", "textContent = 'Copied'"),
    ("'DOI copiado'", "'DOI copied'"),
    ("'Enlace copiado'", "'Link copied'"),
    ("'Cita copiada'", "'Citation copied'"),
    ("'Citas copiadas'", "'Citations copied'"),
    ("`, ${n} ${n === 1 ? 'resultado' : 'resultados'}`", "`, ${n} ${n === 1 ? 'result' : 'results'}`"),
    ('<h3>Sin resultados para «${esc(estado.q)}»</h3>', '<h3>No results for “${esc(estado.q)}”</h3>'),
    ("${conFiltros ? 'Prueba a quitar algún filtro, ' : 'Prueba '}con otra palabra o en inglés, o empieza por una de estas búsquedas:", "${conFiltros ? 'Try removing a filter, ' : 'Try '}another word, or start with one of these searches:"),
    ('<h3>Ningún paper cumple estos filtros</h3><p>Amplía el rango de años, revisa el nombre del autor o quita algún filtro.</p>',
     '<h3>No paper matches these filters</h3><p>Widen the year range, check the author name or remove a filter.</p>'),
    ('data-accion="limpiar">Quitar filtros</button>', 'data-accion="limpiar">Clear filters</button>'),
    ('`Buscando también en inglés: <b>${esc(ex.en)}</b>`', '`Also searching for: <b>${esc(ex.en)}</b>`'),
    ("'No se pudieron cargar los resultados. Revisa tu conexión. <button type=\"button\" class=\"btn-sec\" data-accion=\"reintentar\">Reintentar</button>",
     "'Results could not be loaded. Check your connection. <button type=\"button\" class=\"btn-sec\" data-accion=\"reintentar\">Try again</button>"),
    ('<h3>No pudimos conectar con las bibliotecas</h3><p>Puede ser un fallo momentáneo de la conexión. Tus filtros se mantienen.</p><button type="button" class="btn-sec" data-accion="reintentar">Reintentar</button>',
     '<h3>We could not reach the libraries</h3><p>It may be a temporary connection problem. Your filters are kept.</p><button type="button" class="btn-sec" data-accion="reintentar">Try again</button>'),
    ('<span class="lbl">Tus búsquedas recientes:</span>', '<span class="lbl">Your recent searches:</span>'),
    ('aria-label="Sugerencias de búsqueda"', 'aria-label="Search suggestions"'),
    ("'Tus búsquedas'", "'Your searches'"),
    ("'Temas populares'", "'Popular topics'"),
    ('`también «${x.en}»`', '`also “${x.en}”`'),
    ("grupo: 'En español'", "grupo: 'In Spanish'"),
    ('<label class="sr" for="miniInput">Buscar papers</label><input id="miniInput" type="search" placeholder="Buscar papers" enterkeyhint="search"><button type="submit" aria-label="Buscar">',
     '<label class="sr" for="miniInput">Search papers</label><input id="miniInput" type="search" placeholder="Search papers" enterkeyhint="search"><button type="submit" aria-label="Search">'),
    ('<label class="sr" for="searchInput">Buscar papers</label>', '<label class="sr" for="searchInput">Search papers</label>'),
    ("'Atajos de año'", "'Year shortcuts'"),
    ("'Últimos 2 años'", "'Last 2 years'"),
    ("'Últimos 5 años'", "'Last 5 years'"),
    ("'Últimos 10 años'", "'Last 10 years'"),
    ("'Vista de resultados'", "'Results view'"),
    ('aria-label="Vista detallada" title="Vista detallada"', 'aria-label="Detailed view" title="Detailed view"'),
    ('aria-label="Vista compacta" title="Vista compacta"', 'aria-label="Compact view" title="Compact view"'),
    ("(on ? 'Guardado' : 'Guardar')", "(on ? 'Saved' : 'Save')"),
    ("(on ? 'Quitar de mi lista: ' : 'Guardar en mi lista: ')", "(on ? 'Remove from my list: ' : 'Save to my list: ')"),
    ('<span class="txt">Mi lista</span>', '<span class="txt">My list</span>'),
    ("'Mi lista de papers'", "'My list of papers'"),
    ('<h2>Mi lista</h2>', '<h2>My list</h2>'),
    ('aria-label="Cerrar mi lista"', 'aria-label="Close my list"'),
    ('data-exportar="ris">Descargar RIS</button>', 'data-exportar="ris">Download RIS</button>'),
    ('data-exportar="bib">Descargar BibTeX</button>', 'data-exportar="bib">Download BibTeX</button>'),
    ('data-exportar="citas">Copiar citas</button>', 'data-exportar="citas">Copy citations</button>'),
    ('aria-label="Quitar ${esc(x.titulo)}"', 'aria-label="Remove ${esc(x.titulo)}"'),
    ('<p class="lista-vacia">Aún no has guardado ningún paper. Pulsa «Guardar» en cualquier resultado para reunirlo aquí y exportarlo a tu gestor de referencias.</p>',
     '<p class="lista-vacia">You have not saved any papers yet. Press “Save” on any result to collect it here and export it to your reference manager.</p>'),
    ("'Archivo RIS descargado'", "'RIS file downloaded'"),
    ("'Archivo BibTeX descargado'", "'BibTeX file downloaded'"),
    ("toast('Quitado de tu lista')", "toast('Removed from your list')"),
    ("toast('Guardado en tu lista')", "toast('Saved to your list')"),
    ('<span>Filtros quitados</span><button type="button" id="btnDeshacer">Deshacer</button>', '<span>Filters cleared</span><button type="button" id="btnDeshacer">Undo</button>'),
    ("'Mostrar menos ' : 'Leer resumen completo '", "'Show less ' : 'Read full abstract '"),
]

# Palabras que delatan un texto visible que se quedó en español (para el aviso)
DELATORES = re.compile(r'>[^<>{}]*\b(los|las|del|para|resultados?|buscar|papers? de|más|año|Guardar|Quitar|Copiar|Leer)\b[^<>{}]*<', re.I)


def traducir(t):
    faltan = []
    for es, en in T:
        if es in t: t = t.replace(es, en)
        elif en not in t: faltan.append(es[:70])
    # enlaces de idioma: canónica propia y la versión española
    t = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\s*', '', t)
    t = t.replace('</title>', '</title>\n<link rel="canonical" href="' + URL_EN + '">'
                  '<link rel="alternate" hreflang="es" href="' + URL_ES + '"><link rel="alternate" hreflang="en" href="' + URL_EN + '">'
                  '<link rel="alternate" hreflang="x-default" href="' + URL_ES + '">', 1)
    for f in faltan: print('::warning::Research Hub EN: no encontré este texto en la página española:', f)
    return t


def enlazar_es(t):
    """Añade a la página española su canónica y los enlaces a la versión inglesa (si faltan)."""
    if 'hreflang="en"' in t: return t
    links = ('<link rel="alternate" hreflang="es" href="' + URL_ES + '"><link rel="alternate" hreflang="en" href="' + URL_EN + '">'
             '<link rel="alternate" hreflang="x-default" href="' + URL_ES + '">')
    if 'rel="canonical"' not in t: links = '<link rel="canonical" href="' + URL_ES + '">' + links
    return t.replace('</title>', '</title>\n' + links, 1)
