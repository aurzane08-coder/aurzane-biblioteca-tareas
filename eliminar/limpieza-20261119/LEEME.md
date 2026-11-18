# Limpieza del repositorio (19/11/2026)

Nada se ha borrado: todo lo obsoleto está aquí, con la misma ruta que tenía. Para recuperarlo, `git mv` de vuelta.

## workflows/ (23 flujos de un solo uso, ya terminados)
- Rondas de la biblioteca (descarga, descarga3-5, fichas3-7, sondeo): la biblioteca ya está montada; las fichas las mantiene `guias-libros` y `tienda`.
- `univ-sondeo`: sondeo inicial de fuentes de universidades (sustituido por `univ-ruct`, `univ-principales`, `univ-scorecard`).
- `descargar`, `hoja-fotos`, `portadas-candidatas`: revisiones puntuales de documentos y fotos.
- Parches aplicados una vez y sin programación (`parche-ref`, `parche-google`, `parche-limpieza`, `parche-pdf`, `parche-ovp-guia`, `parche-ovp-idiomas`, `parche-htaccess-js`, `parche-cors`, `parche-textos`): su cambio ya está en el servidor; solo se ejecutaban si se editaba su archivo.

## scripts/
Los scripts que solo usaban esos flujos (ninguno los importa ni los llama otro flujo).

## auditoria/
Capturas de rondas de auditoría anteriores (antes, después, r4 a r10...). En `auditoria/` quedan la herramienta, las listas de páginas, el registro de cambios y los dos últimos resultados (`total-final`, `total-r11-oscuro`).

## deploy/
Lotes de despliegue manual de octubre (u1-u8), sustituidos por la carpeta `publicar/`.
